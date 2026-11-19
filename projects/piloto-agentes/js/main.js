'use strict';

const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#menu');
const mobile = window.matchMedia('(max-width: 39.999rem)');

function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  menu.hidden = mobile.matches;
}

menuButton.hidden = false;
closeMenu();
mobile.addEventListener('change', closeMenu);
menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!expanded));
  menu.hidden = expanded;
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && mobile.matches && !menu.hidden) {
    closeMenu();
    menuButton.focus();
  }
});

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    event.preventDefault();
    closeMenu();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' });
    // Move keyboard focus with navigation, including when a mobile link is hidden.
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
    history.replaceState(null, '', link.hash);
  });
});

const form = document.querySelector('#contact-form');
const fields = [...form.querySelectorAll('input, textarea')];
const status = document.querySelector('#form-status');
const validateButton = document.querySelector('#validate-button');

function validateForm(event) {
  event.preventDefault();
  let firstInvalid = null;
  fields.forEach((field) => {
    let error = '';
    if (!field.value.trim()) {
      error = 'Preencha este campo.';
    } else if (field.type === 'email' && field.validity.typeMismatch) {
      error = 'Informe um e-mail válido, como [EMAIL].';
    } else if (field.validity.tooLong) {
      error = `Use no máximo ${field.maxLength} caracteres.`;
    }
    document.getElementById(`${field.id}-error`).textContent = error;
    field.setAttribute('aria-invalid', String(Boolean(error)));
    if (error && !firstInvalid) firstInvalid = field;
  });
  status.textContent = firstInvalid
    ? 'Revise os campos indicados. A mensagem não foi enviada.'
    : 'Validação concluída! Esta é uma confirmação local. Nenhuma mensagem foi enviada ou armazenada.';
  if (firstInvalid) firstInvalid.focus();
}

form.noValidate = true;
form.addEventListener('submit', validateForm);
validateButton.addEventListener('click', validateForm);
validateButton.disabled = false;
fields.forEach((field) => {
  field.addEventListener('input', () => {
    status.textContent = '';
    field.removeAttribute('aria-invalid');
    document.getElementById(`${field.id}-error`).textContent = '';
  });
});
document.querySelector('#year').textContent = String(new Date().getFullYear());
