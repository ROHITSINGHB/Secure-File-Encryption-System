document.addEventListener('DOMContentLoaded', () => {
  // Example: simple client-side form validation can be added here

  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', event => {
      // For demo: prevent submission if password fields are less than 6 chars
      const password = form.querySelector('input[type="password"]');
      if (password && password.value.length < 6) {
        alert('Password must be at least 6 characters long.');
        event.preventDefault();
      }
    });
  });
});
