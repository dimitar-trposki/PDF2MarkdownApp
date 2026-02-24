from django.db import models


class OriginalModelOutput(models.Model):
    """Stores the output text produced by the model."""
    model = models.CharField(max_length=100)
    text = models.TextField()

    class Meta:
        db_table = 'original_model_output'

    def __str__(self):
        return f"Output #{self.id} ({self.model})"


class UserChangedText(models.Model):
    """Stores the user's edited version of the original text (one-to-one relation)."""
    original_output = models.OneToOneField(
        OriginalModelOutput,
        on_delete=models.CASCADE,
        related_name='user_changes'
    )
    text = models.TextField()

    class Meta:
        db_table = 'user_changed_text'

    def __str__(self):
        return f"User edit for Output #{self.original_output_id}"
