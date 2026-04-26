# tests/fixtures

Shared pytest fixtures live here. As of `0.1.0a0`, every test creates
its own minimal fixtures inline (using `tmp_path`). Fixtures move here
when 2+ tests start sharing the same setup.
