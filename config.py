from dynaconf import LazySettings

settings = LazySettings(
    settings_files=["settings.yml"],
    environments=True,
    env="DEVELOPMENT",
    ENVVAR_PREFIX_FOR_DYNACONF=False,
)
