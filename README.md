# mitta-auth
A password-less Python Flask Auth Module

Mitta Auth is a password-less authentication system written for Mitta.us. 

Authentication systems are difficult to implement. A simplified and secure authentication system is presented that prioritizes end user's rights while still remaining easy to implement and use by a developer.

## Passwords Aren't Needed
Over time, passwords become difficult to remember and may be stored in various systems which themselves require passwords for access and which may be comprimised by other means. For example, one site used by a user may be comprimised which exposes that user's account on a second site because the user decided to use the same password.

At the same time, on most sites, passwords may be "ignored" by using forgotten password functions and flow. 

Mitta Auth takes the less common approach and uses a "forgotten password" authentication flow to authenticate users quickly and easily.

## 2FA Security
It is widely believed that SMS and email two factor functionality may be comprimised by attackers. However, most systems which use passwords AND 2FA will still provide some type of password reset functionality for an account. In the case of Coinbase, a reset of 2FA functionality requires a waiting period, if the client used to reset the authentication system has not been in recent communication.

Mitta Auth will eventually implement both SMS and Google Authentication for logins. For the moment, the code implements only SMS and email authentication flows.

## Installing

## Configuring

## Example Use

