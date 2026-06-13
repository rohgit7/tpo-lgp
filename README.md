# Setup and Run

## 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=shakun
DB_USER=postgres
DB_PASSWORD=smthsmth

HF_TOKEN=your_huggingface_token
```

## 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```
