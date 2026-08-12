# Pytest Review Checklist

Use this checklist after adding or changing tests.

- [ ] Test name describes behavior.
- [ ] Test fails for the old bug when practical.
- [ ] Test does not require external LLM/network services.
- [ ] Test does not depend on execution order.
- [ ] Test covers owner and non-owner paths for user-owned data.
- [ ] Test asserts response body when contract matters.
- [ ] Test does not mock away the core behavior.
- [ ] Test setup is readable.
- [ ] Failure message would help locate the broken layer.
- [ ] Missing dependencies are reported as blockers, not success.
