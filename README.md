# Keryu3

This is the Keryu3 Django web application project using Conda for environment management.

## Setup

1. Create and activate the Conda environment:
```bash
conda env create -f environment.yml
conda activate keryu3
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Project Structure

- `keryu3/` - Main project directory
  - `settings.py` - Project settings
  - `urls.py` - Main URL configuration
  - `wsgi.py` - WSGI configuration
  - `asgi.py` - ASGI configuration

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Updating Dependencies

If you need to update dependencies, modify the `environment.yml` file and run:
```bash
conda env update -f environment.yml
``` 