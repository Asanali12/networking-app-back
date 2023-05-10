from socialApp.settings import s3_client


def upload_image_to_aws_storage(bucket_name, contents, destination_blob_name):
    s3_client.put_object(
        Bucket=bucket_name,
        Key=destination_blob_name,
        Body=contents,
        ContentType='image/jpg',
        ACL='public-read',
    )
    return f'https://storage.yandexcloud.net/{bucket_name}/{destination_blob_name}'
