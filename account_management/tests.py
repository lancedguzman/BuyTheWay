from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

# Use get_user_model() to dynamically retrieve your UserProfile model
User = get_user_model()

class UserProfileTests(TestCase):
    
    def setUp(self):
        """Set up valid base data for the tests."""
        self.valid_email = "testuser@buytheway.com"
        self.valid_password = "SecurePassword123!"
        self.valid_phone = "09123456789"
    
    # UserProfileManager Tests
    def test_create_user_success(self):
        """Test creating a standard user with valid credentials."""
        user = User.objects.create_user(
            email=self.valid_email,
            password=self.valid_password,
            user_type='B',
            phone_number=self.valid_phone,
            first_name="Juan",
            last_name="Dela Cruz"
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertTrue(user.check_password(self.valid_password))
        self.assertEqual(user.user_type, 'B')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email_raises_error(self):
        """Test that user creation fails if no email is provided."""
        with self.assertRaisesMessage(ValueError, "Email must be provided"):
            User.objects.create_user(
                email="",
                password=self.valid_password
            )

    def test_create_superuser_success(self):
        """Test creating a superuser sets the correct administrative flags."""
        admin_user = User.objects.create_superuser(
            email="admin@buytheway.com",
            password=self.valid_password
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_superuser_invalid_staff_flag(self):
        """Test that a superuser cannot be created with is_staff=False."""
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            User.objects.create_superuser(
                email="admin2@buytheway.com",
                password=self.valid_password,
                is_staff=False
            )

    def test_create_superuser_invalid_superuser_flag(self):
        """Test that a superuser cannot be created with is_superuser=False."""
        with self.assertRaisesMessage(ValueError, "Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                email="admin3@buytheway.com",
                password=self.valid_password,
                is_superuser=False
            )

    # UserProfile Model Validation Tests
    def test_valid_philippine_phone_numbers(self):
        """Test that valid Philippine phone formats pass validation."""
        valid_numbers = ["09123456789", "+639123456789"]
        
        for number in valid_numbers:
            user = User(
                email=f"phone_{number}@buytheway.com",
                user_type='S',
                phone_number=number
            )
            try:
                # Exclude password from the validation check
                user.full_clean(exclude=['password']) 
            except ValidationError:
                self.fail(f"full_clean() raised ValidationError unexpectedly for valid number: {number}")

    def test_invalid_philippine_phone_number_raises_error(self):
        """Test that invalid phone formats trigger a ValidationError."""
        invalid_numbers = [
            "123456789",      # Missing prefix
            "0912345678",     # Too short
            "+6391234567890", # Too long
            "08123456789",    # Invalid network prefix
            "abc12345678"     # Contains letters
        ]
        
        for number in invalid_numbers:
            user = User(
                email=f"badphone_{number}@buytheway.com",
                user_type='B',
                phone_number=number
            )
            with self.assertRaises(ValidationError):
                # Exclude password here as well
                user.full_clean(exclude=['password'])

    def test_user_string_representation(self):
        """Test the __str__ method of the UserProfile model."""
        user = User.objects.create_user(
            email=self.valid_email,
            password=self.valid_password,
            first_name="Maria",
            last_name="Clara",
            user_type='S',
            phone_number=self.valid_phone
        )
        expected_string = f"Maria Clara ({self.valid_email})"
        self.assertEqual(str(user), expected_string)


class EmailVerificationTokenTests(TestCase):
    
    def setUp(self):
        """Set up base data for email token tests."""
        self.user = User.objects.create_user(
            email="tokenuser@buytheway.com",
            password="SecurePassword123!",
            user_type='B',
            phone_number="09123456789"
        )

    def test_token_creation_and_otp_generation(self):
        """Test generating an OTP and assigning it to an EmailVerificationToken."""
        # Import here to avoid circular dependencies if models are heavily linked
        from .models import EmailVerificationToken 

        otp_code = EmailVerificationToken.generate_otp()
        self.assertEqual(len(otp_code), 6)
        self.assertTrue(otp_code.isdigit())

        token = EmailVerificationToken.objects.create(
            user=self.user,
            otp=otp_code
        )
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.otp, otp_code)
        self.assertFalse(token.is_expired())

    def test_token_expiration(self):
        """Test that the token correctly reports as expired after 10 minutes."""
        from .models import EmailVerificationToken
        
        token = EmailVerificationToken.objects.create(
            user=self.user,
            otp="123456"
        )
        
        # Manually backdate the created_at field by 11 minutes
        token.created_at = timezone.now() - timedelta(minutes=11)
        token.save()
        
        self.assertTrue(token.is_expired())

    def test_token_string_representation(self):
        """Test the __str__ method of the EmailVerificationToken."""
        from .models import EmailVerificationToken
        
        token = EmailVerificationToken.objects.create(
            user=self.user,
            otp="123456"
        )
        expected_string = f"OTP for {self.user.email}"
        self.assertEqual(str(token), expected_string)


class SellerIDVerificationTests(TestCase):

    def setUp(self):
        """Set up a valid seller user for ID verification tests."""
        self.seller = User.objects.create_user(
            email="seller@buytheway.com",
            password="SecurePassword123!",
            user_type='S',  # Must be Seller based on limit_choices_to
            phone_number="09987654321"
        )
        
        # Create dummy images for file validation tests
        self.valid_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x00\x00\x00',
            content_type='image/jpeg'
        )
        self.invalid_file = SimpleUploadedFile(
            name='test_document.pdf',
            content=b'%PDF-1.4...',
            content_type='application/pdf'
        )

    def test_seller_id_creation_defaults(self):
        """Test creating a SellerIDVerification record sets default status to pending."""
        from .models import SellerIDVerification
        
        verification = SellerIDVerification(
            seller=self.seller,
            id_type='drivers_license',
            id_photo=self.valid_image,
            selfie_with_id=self.valid_image
        )
        verification.save()
        
        self.assertEqual(verification.status, 'pending')
        self.assertIsNone(verification.reviewed_at)

    def test_seller_id_file_extension_validation(self):
        """Test that FileExtensionValidator catches invalid file types like PDFs."""
        from .models import SellerIDVerification
        
        verification = SellerIDVerification(
            seller=self.seller,
            id_type='passport',
            id_photo=self.invalid_file, # Invalid extension
            selfie_with_id=self.valid_image
        )
        
        with self.assertRaises(ValidationError) as context:
            # full_clean() executes validators like FileExtensionValidator
            verification.full_clean()
            
        self.assertIn('id_photo', context.exception.message_dict)

    def test_seller_id_string_representation(self):
        """Test the __str__ method of the SellerIDVerification."""
        from .models import SellerIDVerification
        
        verification = SellerIDVerification(
            seller=self.seller,
            id_type='philsys',
            status='approved',
            id_photo=self.valid_image,
            selfie_with_id=self.valid_image
        )
        verification.save()
        
        expected_string = f"ID Verification — {self.seller.email} [Approved]"
        self.assertEqual(str(verification), expected_string)
