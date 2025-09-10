document.addEventListener('DOMContentLoaded', () => {

  // Dashboard navigation
  const navLinks = document.querySelectorAll('.sidebar-menu a, .profile-dropdown a.nav-link, .nav-link-button');
  const views = document.querySelectorAll('.dashboard-view');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const viewId = link.getAttribute('data-view');
      document.querySelectorAll('.sidebar-menu a').forEach(nav => nav.classList.remove('active'));
      const activeSidebarLink = document.querySelector(`.sidebar-menu a[data-view="${viewId}"]`);
      if (activeSidebarLink) activeSidebarLink.classList.add('active');
      views.forEach(view => view.classList.remove('active'));
      const viewToShow = document.getElementById(viewId);
      if(viewToShow) viewToShow.classList.add('active');
      const profileDropdown = document.getElementById('profileDropdown');
      if (link.closest('.profile-dropdown') && profileDropdown) profileDropdown.classList.remove('show');
    });
  });

  // Profile dropdown toggle
  const profileIcon = document.getElementById('profileIcon');
  const profileDropdown = document.getElementById('profileDropdown');
  if (profileIcon) {
    profileIcon.addEventListener('click', () => {
      if(profileDropdown) profileDropdown.classList.toggle('show');
    });
  }
  window.addEventListener('click', (e) => {
    if (profileIcon && !profileIcon.contains(e.target) && profileDropdown && !profileDropdown.contains(e.target)) {
      profileDropdown.classList.remove('show');
    }
  });

  // Drag and Drop functionality
  document.querySelectorAll('.file-upload-area').forEach(dropArea => {
    const fileInput = dropArea.nextElementSibling;
    const fileNameDisplay = dropArea.querySelector('.file-name');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => { e.preventDefault(); e.stopPropagation(); }, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-over'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-over'), false);
    });
    dropArea.addEventListener('drop', (e) => {
      fileInput.files = e.dataTransfer.files;
      if(fileNameDisplay && fileInput.files.length) fileNameDisplay.textContent = fileInput.files[0].name;
    }, false);
    dropArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      if(fileNameDisplay && e.target.files.length) fileNameDisplay.textContent = e.target.files[0].name;
    });
  });

  // Function to show a dynamic toast message
  const showDynamicToast = (message, category = 'error') => {
      const toastContainer = document.getElementById('toast-container');
      if (!toastContainer) return;

      const toast = document.createElement('li');
      toast.className = category;
      toast.textContent = message;
      toastContainer.appendChild(toast);

      setTimeout(() => toast.classList.add('show'), 10); // Delay to allow CSS transition
      setTimeout(() => {
          toast.classList.remove('show');
          toast.addEventListener('transitionend', () => toast.remove());
      }, 5000);
  };
  
  // Asynchronous Form Submission for Encrypt/Decrypt
  const handleCryptoFormSubmit = async (form, button) => {
    button.classList.add('loading');
    button.disabled = true;
    const formData = new FormData(form);
    
    try {
      const response = await fetch(form.action, { method: 'POST', body: formData });
      if (response.ok) {
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.includes('attachment')) {
          const filename = disposition.split('filename=')[1].replace(/"/g, '');
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
          showDynamicToast(form.id === 'encryptForm' ? 'File encrypted successfully!' : 'File decrypted successfully!', 'success');
          
          // Update stats on the page without full reload
          const encryptedCount = document.getElementById('encrypted-count');
          const decryptedCount = document.getElementById('decrypted-count');
          if (form.id === 'encryptForm' && encryptedCount) {
              encryptedCount.textContent = parseInt(encryptedCount.textContent) + 1;
          } else if (form.id === 'decryptForm' && decryptedCount) {
              decryptedCount.textContent = parseInt(decryptedCount.textContent) + 1;
          }
        }
      } else {
        const errorData = await response.json();
        if (errorData.error) {
          showDynamicToast(errorData.error, 'error');
        }
      }
    } catch (error) {
      showDynamicToast('A network error occurred. Please try again.', 'error');
    } finally {
      button.classList.remove('loading');
      button.disabled = false;
    }
  };

  const encryptForm = document.getElementById('encryptForm');
  if (encryptForm) {
    encryptForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCryptoFormSubmit(encryptForm, document.getElementById('encryptButton'));
    });
  }

  const decryptForm = document.getElementById('decryptForm');
  if (decryptForm) {
    decryptForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCryptoFormSubmit(decryptForm, document.getElementById('decryptButton'));
    });
  }
});
