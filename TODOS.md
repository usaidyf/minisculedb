# TODOs

## Backlog
- Add option for verbose server mode
- Add nested dict support with value parsing at every level.
- Standardize the response format for better programmatic parsing on the client side. (e.g. use JSON)
- Create a WOL (write only log) for all the transactions on the database to be able to recover from any unexpected crashes or data loss. Wipe off the log file completely after every safe exit of the server side program.

## In Progress


## Things to remmber
- The db is primarily to be used within applications (not production level though) that's why it's primary mode isn't verbose and is pretty much integratable. That said, users can use the verbose mode if they want a "console-like" experience to try out.