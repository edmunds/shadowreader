## Contributing

Please send a GitHub Pull Request with a clear list of what you've done

Currently, only Python3.6+ and AWS is supported

Please follow PEP8, but the line length limit may be ignored if following it would make the code uglier.

## Reporting issues

* Describe what you expected to happen.
* If possible, include an example to help
  us identify the issue.
* Describe what actually happened. Include the full traceback if there was an
  exception.
* List your Python version, any associated AWS resources you are having trouble with

## Testing

Testing is conducted with Pytest and tests are located inside /tests. Please write new tests for new code you create.

Running the tests

```
Run the basic test suite:
    pytest

Running test coverage:
    pytest --cov .

Running test coverage with HTML report:
    pytest --cov . --cov-report html --cov-branch
    # then open htmlcov/index.html
```

Read more about `coverage <https://coverage.readthedocs.io>`
