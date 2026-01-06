# Made by Louis Chatain (that's me)

# Technologies

<ul>
    <li>Python</li>
    <li>FastApi</li>
    <li>SQLAlchemy</li>
    <li>Alembic</li>
    <li>Pytest</li>
    <li>Pydentic</li>
</ul>

# Features

Here's what you can do with this API:
<ul>
    <li>CRUD opration on a User.</li>
    <li>Create a User.</li>
    <li>Log in into that Account.</li>
</ul>

# The Process

1. Project Setup and Dependencies

    Initialized the project environment using Python.

    Installed core dependencies: FastAPI for the web framework, SQLAlchemy (with an async driver) for the ORM to interact with the database, and Pydantic for data validation and defining schemas.

2. Database Configuration

    Set up a PostgreSQL database connection using SQLAlchemy and configured the session management.

    Defined the database models using SQLAlchemy's Declarative base.

    Setup Alembic for the database upgrades and history.

3. User Authentication and Authorization

    Implemented user creation and login endpoints.

    Utilized werkzeug for securely hashing and verifying user passwords.

    Integrated OAuth2 (specifically the Password flow) for issuing access tokens upon successful login.

    Implemented JWT (JSON Web Tokens) for stateless user authentication. The JWTs are signed and contain the user ID, allowing the API to identify the authenticated user on subsequent requests.

    Created a dependency function to extract and validate the JWT from the request header, ensuring that only authenticated and authorized users can access protected routes.

4. CRUD Operations Implementation

    User: Developed endpoints for creating a user and fetching user details.

5. Data Validation

    Leveraged Pydantic models to define the expected structure and validation rules for all incoming request data (e.g., email format, required fields for a post) and outgoing response data. This ensures data integrity and consistency.

6. Testing

    Wrote unit and integration tests using Pytest to ensure all endpoints, database operations, and authentication logic functioned as expected. This included testing successful operations, error handling, and authorization failures.


# What I Learned

1. Object-Relational Mapping (ORM)

    Deepened my understanding of SQLAlchemy, mastering how to define complex database schemas, manage sessions, and execute queries, moving beyond raw SQL to more manageable and type-safe data interactions.

2. API Security Essentials

    Solidified my knowledge of implementing a robust authentication flow using the OAuth2 standard.

    Understood the critical role of JWTs for securely transmitting information between parties and for managing user sessions in a stateless environment.

    Learned the best practice of using libraries like werkzeug for password hashing to prevent storing plain-text passwords.

3. Data Modeling and Validation

    Experienced firsthand the power of Pydantic in enforcing data integrity. This library simplifies the process of validating input data against defined schemas, significantly reducing bugs and making the API contract clear.

4. Test-Driven Thinking

    Learned how to effectively use Pytest to create comprehensive test suites. Writing tests concurrently with feature development proved invaluable, helping to catch bugs early and ensuring the system remains stable as new features are added.

Overall growth:
Each part of this project helped me understand more about building apps, managing...
It was about solving problems, learning new things, and improving my skills for future work.

# How can it be improved?

<ul>
    <li>Plan out in advence the structure of the project. (Learned it the hard way.)</li>
    <li>Add video uploads.</li>
    <li>Add likes, re-tweet and views under posts and comments.</li>
    <li>Add Following users and follow count.</li>
</ul>

# Running The Project Locally

To run the project in your local environment, follow these steps:

1.Clone the repository to your local machine.
2.Create a Python virtual environnent using Python3.13
3.Make sure the requirements have been installed.
4.Check the "launch.sh" file to potentially change the host or/and port.
5.Run the lauch.sh file.
6.Open http://127.0.0.1:8000/docs (or the address shown in your console) in your web browser to view the Swagger documentation.

# Running The Project On Docker

Go see this other project's README.md
