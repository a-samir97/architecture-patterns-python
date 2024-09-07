# Architecture Patterns with Python 

### Four key design patterns:

- Repository Pattern: abstraction over persistant storage
- Service Layer: pattern to define the start and the end of the user cases
- Unit of Work Pattern: provide atomic operations
- Aggregate Pattern: to enforce the integrity of the data

__________________________________________________________________________

# Chapter 1 (DDD - Domain Model)

- DDD in nutshell -> most important thing about software is that it provides a useful model of the problem.
- Domain model: is the mental map that business owners have of their businesses.
- Value object is any domain object that is uniquely identified by the data it holds.
- Entity unlike values, have identify equality. We can change their values and still recognizbaly the same thing.

__________________________________________________________________________

# Chapter 2 (Repository Pattern)
- Repository pattern: a simplifying abstraction over data storage, allowing us to decouple our model layer from the data layer
- Normal ORM way: Model depends on ORM, inverting the dependency: ORM depends on Model
- Building fakes for your abstractions is an excellent way to get design feedback: if it’s hard to fake, the abstraction is probably too complicated
- Port is the interface between our application and whatever it is we wish to abstract away
- Adapter: is the implementation behind that interface 

_____________________________________________________________________________

# Chapter 6 (Unit Of Work Pattern)
- The unit of work pattern is abstraction around data integrity
    - helps to enforce consistency of our domain model, and improves performance
- works closely with Repository and Service layer patterns
    - completes abstractions over data access by representing atomic updates, each of service-layer use cases runs in a single unit of work that succeeds or failas a block
- Lovely case for a `Context Manager`
    - `Context Manager` idiomatic way of defining and managing resources in Python. we can use `context manager` to automatically roll back the process at the end of the request, which means the system is safe by default.
- SQLAlchemy already implements (UOW) Pattern 
_____________________________________________________________________________

# Chapter 7 (Aggregates and Consistency Boundaries)
- Aggregate Pattern: is just a domain object that contains other domain objects and lets us treat the whole collection as a single unit
- Aggregates are your entrypoint into the domain model
    - by restricting the number of ways that can be changed, which make the system easier.
- Aggregates are in charge of a consistency boundary
    - aggregate job to check the objects within it are consistent with each other and with business rules and to reject changes that break the rules of our system.
- Aggregates and Concurrency issues go together
    - thinking about transactions and locks
