const SITE_ONE_URL = 'http://localhost:9090'

describe('Desperately try to read a cookie after origin', () => {
  it("Won't work", () => {
    cy.visit(`${SITE_ONE_URL}`)
    cy.contains('Login').click()

    cy.origin("https://login.microsoftonline.com", () => {
      // We should see the Microsoft login page
      cy.url().should("include", "login.microsoftonline.com");

      // Fill in the username and password from env vars
      cy.get('input[name="loginfmt"]').type(
        Cypress.env("MICROSOFT_LOGIN_EMAIL"),
        { log: false }
      );
      cy.get('input[type="submit"]').click();

      cy.get('input[name="passwd"]', { timeout: 10000 }).should("be.visible");
      cy.get('input[name="passwd"]').type(
        Cypress.env("MICROSOFT_LOGIN_PASSWORD"),
        {
          log: false,
        }
      );
      cy.get('input[type="submit"]').click();

      // If there is a "Stay signed in?" prompt, click "No"
      cy.get("input[type='button'][value='No']").click();
    })
  })
})