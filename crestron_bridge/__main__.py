import uvicorn

from crestron_bridge.gunicorn_runner import GunicornApplication
from crestron_bridge.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    if settings.reload:
        uvicorn.run(
            "crestron_bridge.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        # We choose gunicorn only if reload
        # option is not used, because reload
        # feature doen't work with Uvicorn workers.
        GunicornApplication(
            "crestron_bridge.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            timeout=600,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',  # noqa: WPS323
        ).run()


if __name__ == "__main__":
    main()
