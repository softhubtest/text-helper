try:
    import starlette
    print(f"Starlette version: {starlette.__version__}")
    from starlette.middleware import gzip
    print(f"gzip module content: {dir(gzip)}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
