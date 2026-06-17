from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

                                                              

    DATABASE_URL:  str

    OPENAI_API_KEY:  str

    GEOAPIFY_API_KEY:  str

    OPENWEATHER_API_KEY:  str

    AVIATIONSTACK_API_KEY:  str

    SECRET_KEY:  str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str | None = None

    model_config = SettingsConfigDict(

        env_file=".env",                                            

        extra="ignore"                                                       

    )

                                                     

settings = Settings()
