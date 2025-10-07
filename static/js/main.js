// static/js/main.js

$(document).ready(function() {
  // Confirm delete dialogs for all delete forms
  $('form').on('submit', function(e) {
    const $form = $(this);
    // Only confirm for forms with .confirm-delete class OR with a delete button icon
    if ($form.find('button[type="submit"] i.bi-trash-fill').length > 0 || $form.hasClass('confirm-delete')) {
      const confirmed = confirm("Are you sure you want to delete this item?");
      if (!confirmed) {
        e.preventDefault();
        return false;
      }
    }
  });

  // Toggle dark/light theme
  // Store theme preference in localStorage
  const themeToggleBtn = $('#themeToggleBtn');

  function applyTheme(theme) {
    if (theme === 'light') {
      $('body').addClass('light-theme').removeClass('dark-theme bg-dark text-light');
      $('.table').removeClass('table-dark').addClass('table-light');
      $('.navbar').removeClass('navbar-dark bg-dark').addClass('navbar-light bg-light');
      themeToggleBtn.html('<i class="bi bi-moon"></i>'); // show moon icon
    } else {
      $('body').removeClass('light-theme').addClass('dark-theme bg-dark text-light');
      $('.table').removeClass('table-light').addClass('table-dark');
      $('.navbar').removeClass('navbar-light bg-light').addClass('navbar-dark bg-dark');
      themeToggleBtn.html('<i class="bi bi-sun"></i>'); // show sun icon
    }
  }

  function getSavedTheme() {
    return localStorage.getItem('theme') || 'dark';
  }

  function saveTheme(theme) {
    localStorage.setItem('theme', theme);
  }

  // Initial set theme on page load
  applyTheme(getSavedTheme());

  themeToggleBtn.on('click', function() {
    const currentTheme = getSavedTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    saveTheme(newTheme);
  });
});

$(document).ready(function() {
  var deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'))

  // Site delete button handler
  $('.btn-delete-site').on('click', function(e) {
    e.preventDefault()
    let siteId = $(this).data('site-id')
    let siteName = $(this).data('site-name')
    $('#confirmDeleteModalLabel').text('Delete Site')
    $('#modalDeleteBody').html(`Are you sure you want to delete the site "<strong>${siteName}</strong>"?`)
    $('#modalDeleteForm').attr('action', `/site_data/delete/${siteId}`)
    deleteModal.show()
  })

  // Report delete button handler
  $('.btn-delete-report').on('click', function(e) {
    e.preventDefault()
    let reportId = $(this).data('report-id')
    let ticket = $(this).data('report-ticket')
    let siteName = $(this).data('report-site')
    $('#confirmDeleteModalLabel').text('Delete Report')
    $('#modalDeleteBody').html(`Are you sure you want to delete the report for site "<strong>${siteName}</strong>" with ticket ID "<strong>${ticket}</strong>"?`)
    $('#modalDeleteForm').attr('action', `/daily_problem_report/delete/${reportId}`)
    deleteModal.show()
  })
})
