from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class CustomRichTextField(RichTextField):
    def __init__(self , *args , **kwargs):
        super(CustomRichTextField , self).__init__(*args , **kwargs)

    class Meta:
        abstract = True