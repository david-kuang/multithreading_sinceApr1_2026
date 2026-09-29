// A tiny "hello world" app — deliberately simple so it's easy to watch
// OpenCode read it, explain it, and modify it.

function greet(name = "world") {
  return `Hello, ${name}!`;
}

console.log(greet());

module.exports = { greet };
