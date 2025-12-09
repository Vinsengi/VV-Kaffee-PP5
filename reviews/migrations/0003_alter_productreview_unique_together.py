from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0002_experiencefeedback_productreview_delete_review"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productreview",
            unique_together=set(),
        ),
    ]
