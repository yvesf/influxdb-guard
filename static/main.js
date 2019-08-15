// Generate random token string 

const KEY_LENGTH = 20;
const ALPHABET_BASE58 = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ';

function genToken() {
  const rand_buffer = Array.from(window.crypto.getRandomValues(new Uint32Array(KEY_LENGTH)));
  const rand_chars = rand_buffer.map(elem => ALPHABET_BASE58.charAt(Math.round(elem/4294967295*58)));
  const token = rand_chars.join("");

  document.getElementById("tokenField").value = token;
}
