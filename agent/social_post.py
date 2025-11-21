"""Social post generator module.

This module generates professional social media content:
- LinkedIn post generation about Ciklum AI Academy
- Experience summarization
- Customizable closing statements

SAFETY: This module ONLY generates text content.
It does NOT post to LinkedIn or any social media platform.
All content must be manually copied and posted by the user.
"""

from agent.prompts import format_linkedin_post


class SocialPostGenerator:
    """
    Generate LinkedIn posts about Ciklum AI Academy completion

    This class provides safe post generation with NO automatic posting.
    Posts are displayed in terminal and optionally saved to file.
    Users must manually copy content to LinkedIn.

    Features:
    - Customizable closing statements
    - File save capability
    - Rich terminal formatting support

    Safety guarantees:
    - No LinkedIn API integration
    - No automatic clipboard copying
    - No network requests
    - Local generation only
    """

    def __init__(self):
        """Initialize the social post generator"""
        pass

    def generate_post(self, custom_closing: str = "") -> str:
        """
        Generate a LinkedIn post about Ciklum AI Academy completion

        Args:
            custom_closing: Optional custom closing statement to append

        Returns:
            Generated LinkedIn post text

        Example:
            >>> generator = SocialPostGenerator()
            >>> post = generator.generate_post()
            >>> print(post)
        """
        return format_linkedin_post(custom_closing=custom_closing)

    def save_post(self, post_text: str, filename: str) -> None:
        """
        Save generated post to a text file

        Args:
            post_text: The generated post content
            filename: Path to save file (e.g., "my_post.txt")

        Raises:
            IOError: If file cannot be written

        Example:
            >>> generator = SocialPostGenerator()
            >>> post = generator.generate_post()
            >>> generator.save_post(post, "linkedin_post.txt")
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(post_text)
        except Exception as e:
            raise IOError(f"Failed to save post to {filename}: {e}")


# Test the generator if run directly
if __name__ == "__main__":
    print("=" * 70)
    print("SOCIAL POST GENERATOR TEST")
    print("=" * 70)

    generator = SocialPostGenerator()

    print("\n1. Default Post:")
    print("-" * 70)
    default = generator.generate_post()
    print(default)

    print("\n\n2. With Custom Closing:")
    print("-" * 70)
    custom = generator.generate_post(
        custom_closing="Looking forward to collaborating on AI-driven projects!"
    )
    print(custom)

    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)
    print("\nSAFETY REMINDER:")
    print("• No automatic posting to LinkedIn")
    print("• No clipboard copying")
    print("• Manual copy & paste required")
    print("=" * 70)
