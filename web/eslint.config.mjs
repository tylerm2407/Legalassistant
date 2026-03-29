import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

const eslintConfig = [
  ...nextCoreWebVitals,
  {
    rules: {
      "no-console": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
];

export default eslintConfig;
