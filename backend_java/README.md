# Contact Directory API

A recruiter-friendly Java backend sample that manages business contacts through a versioned REST API. It demonstrates a layered Spring Boot design, MongoDB persistence, request validation, duplicate detection, consistent error responses, and pagination.

## Stack

- Java 21 and Spring Boot 4.1.2
- Spring Web MVC and Jakarta Bean Validation
- Spring Data MongoDB
- MongoDB 8 for local development
- Spring Boot Actuator health and application info endpoints

## Architecture

```text
api/          REST controller, request/response records, validation errors
domain/       MongoDB document and contact status
service/      business rules, normalization, timestamps, and error handling
repository/   Spring Data MongoDB repository
```

The API uses constructor injection and keeps persistence documents separate from the HTTP request and response models. Contact emails are normalized to lowercase and protected by a unique MongoDB index.

## Run locally

Prerequisites: Java 21, Maven 3.6.3+, and Docker with Docker Compose.

Start MongoDB from this directory:

```bash
docker compose up -d
```

Start the API:

```bash
mvn spring-boot:run
```

The app connects to `mongodb://localhost:27017/contact_directory` by default. To connect to MongoDB Atlas or another MongoDB server, set `MONGODB_URI` before starting the app:

```powershell
$env:MONGODB_URI = "mongodb+srv://<user>:<password>@<cluster>/contact_directory"
mvn spring-boot:run
```

```bash
export MONGODB_URI="mongodb+srv://<user>:<password>@<cluster>/contact_directory"
mvn spring-boot:run
```

Health and app metadata are available at `/actuator/health` and `/actuator/info`.

## API

Base path: `/api/v1/contacts`

| Method | Route | Behavior |
| --- | --- | --- |
| `GET` | `/api/v1/contacts` | List contacts with pagination and sorting (`page`, `size`, `sort`) |
| `GET` | `/api/v1/contacts/{id}` | Fetch one contact |
| `POST` | `/api/v1/contacts` | Create a contact; returns `201 Created` and a `Location` header |
| `PUT` | `/api/v1/contacts/{id}` | Replace a contact |
| `DELETE` | `/api/v1/contacts/{id}` | Delete a contact; returns `204 No Content` |

Example create request:

```json
{
  "fullName": "Jordan Lee",
  "email": "jordan.lee@example.com",
  "company": "Northstar Labs",
  "status": "LEAD",
  "notes": "Met at the product leadership meetup"
}
```

Example calls:

```bash
curl "http://localhost:8080/api/v1/contacts?page=0&size=10"
curl -X POST "http://localhost:8080/api/v1/contacts" \
  -H "Content-Type: application/json" \
  -d '{"fullName":"Jordan Lee","email":"jordan.lee@example.com","company":"Northstar Labs","status":"LEAD","notes":"Met at the product leadership meetup"}'
```

Invalid input returns `400`, a missing contact returns `404`, and a duplicate email returns `409`. Error bodies include a timestamp, status, message, request path, and field validation details where applicable.

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27017/contact_directory` | MongoDB connection string |
| `PORT` | `8080` | HTTP port |

No database credentials are committed. Supply credentials through the connection string when using a protected MongoDB deployment.
