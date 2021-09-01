# Changelog

This changelog started with version 0.3.0 (Aug 2021)

## [0.3.1] - 2021-09-01

### Changed

- Unpin ipykernel 6 dependency so it doesn't upgrade/break single-user deployments
- Check `ipykernel.__version__` to determine whether to use `nbclient.util.just_run` in `ipython_blocking.py`

## [0.3.0] - 2021-08-28

### Changed

- Uses `nbclient.util.just_run` to handle the asynchronous-as-of-ipykernel-6.x `get_ipython().shell.kernel.do_one_iteration()`
- Pin dependency to ipykernel 6.x. For users on older ipykernel versions, use `ipython_blocking<0.3`
