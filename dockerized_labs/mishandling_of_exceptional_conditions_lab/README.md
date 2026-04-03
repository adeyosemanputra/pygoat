# Mishandling of Exceptional Conditions Lab

This lab demonstrates how improper exception handling can expose sensitive information to users. It is part of the PyGoat project and runs as a standalone Flask application.

## Vulnerability Description

The lab includes a pricing calculator that fails unsafely. It returns full stack traces and exception details to the user whenever an error occurs. This behavior exposes internal implementation details and can be exploited by attackers.

## Lab Solution

Trigger a failure to observe error leakage:

1. Set **Discount Divisor** to `0` to cause a divide-by-zero error.
2. Use an invalid **Coupon Code** (for example, `FREE100`) to trigger a key lookup failure.
3. Enter a non-numeric **Order Total** (for example, `abc`) to trigger a numeric parsing error.

All of these cases return detailed stack traces in the response, demonstrating the risk of mishandled exceptions.

## Security Notes

This is a deliberately vulnerable application for educational purposes. Do not use these practices in production code.
