# Security Policy

Querya handles database credentials and query data, so we take security reports seriously.

## Supported versions

We fix security issues in the **latest release** of each project. Please reproduce the problem on the latest version before reporting.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately using one of:

- GitHub's **Report a vulnerability** button on the *Security* tab of the affected repository
- Email **contact@queryahub.com** with the subject `[security] <project>: <short summary>`

Include, where possible:

- the affected project and version, and your OS
- a description of the issue and its impact
- steps or a proof of concept to reproduce it

## What to expect

- We acknowledge your report within **3 working days**.
- We assess it and share a plan or a request for more information within **7 days**.
- We credit you in the release notes once a fix ships, unless you prefer to stay anonymous.

## Scope

In scope: the Querya projects in this organization, including credential storage, handling of connection secrets, the extension host and RPC bridge, and update/packaging integrity.

Out of scope: vulnerabilities in third-party dependencies with no demonstrable impact on Querya, and issues that require an already compromised machine or OS account.
