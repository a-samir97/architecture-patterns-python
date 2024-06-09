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

