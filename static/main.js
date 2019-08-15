// Generate random token string
// TOKEN_LENGTH is provided by a inline script
const ALPHABET_BASE58 = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ';

const genToken = () => {
  const rand_buffer = Array.from(window.crypto.getRandomValues(new Uint32Array(TOKEN_LENGTH)));
  const rand_chars = rand_buffer.map(elem => ALPHABET_BASE58.charAt(Math.round(elem/4294967295*58)));
  const token = rand_chars.join("");

  document.getElementById("tokenField").value = token;
};
