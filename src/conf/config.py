from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class MailSettings(BaseSettings):
    username: str='user@gmail.com'
    password: str='password'
    mail_from: str='user'
    port: int='1234'
    server: str='smtp.gmail.com'

    # in .env file all constants for mailing wil be 
    # like MAIL_USERNAME, MAIL_PASSWORD and so on
    model_config = SettingsConfigDict(env_prefix='mail_')


class CloudinarySettings(BaseSettings):
    cloud_name: str='cloud'
    api_key: str='key'
    api_secret: str='secret'
    folder: str='folder'

    # in .env file all constants for Cloudinary wil be 
    # like CLOUDINARY_CLOUD_NAME CLOUDINARY_API_KEY and so on
    model_config = SettingsConfigDict(env_prefix='cloudinary_')


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    
    # to access mail settings user setting.mail
    mail: MailSettings

    # to access Cloudinary settings user settings.cloudinary
    cloudinary: CloudinarySettings


settings = Settings(mail=MailSettings(), cloudinary=CloudinarySettings())