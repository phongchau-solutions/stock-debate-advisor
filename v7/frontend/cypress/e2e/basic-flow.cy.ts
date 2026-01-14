describe('Stock Debate Advisor basic flow', () => {
  it('loads analysis page and toggles theme', () => {
    cy.visit('/');
    cy.contains('Debate & Analysis').should('be.visible');
    cy.findByRole('button', { name: /toggle theme/i }).click({ force: true });
  });
});


