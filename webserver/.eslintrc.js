module.exports = {
    "extends":  [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    "env": {
        "es6": true,
        "node": false, 
        "browser": true
    },
    "plugins": ["react"],
    "parserOptions": {
        "ecmaVersion": 6,
        "sourceType": "module",
        "ecmaFeatures": {
            "jsx": true
        }
    },
    "rules": {
        "no-undef": 1,
        "no-unused-vars": 1,
        "no-console": 0,
        "indent": ["error", 4],
        "no-unreachable" : ["error"],
        "no-unexpected-multiline": ["error"],
        "semi": ["error", "always"],
        "semi-spacing": ["error"],
        "no-extra-semi": ["error"],
        "brace-style": ["error", "1tbs"],
        "quotes": ["error", "single"]
    }
};