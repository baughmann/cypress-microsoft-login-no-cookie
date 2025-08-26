const { defineConfig } = require("cypress");
import dotenv from "dotenv";

dotenv.config({ path: "../.env" });

module.exports = defineConfig({
  e2e: {
    chromeWebSecurity: false,
    experimentalOriginDependencies: true,
    experimentalModifyObstructiveThirdPartyCode: true,
    modifyObstructiveCode: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    blockHosts: [],
    injectDocumentDomain: true,
  },
  env: {
    // Map all environment variables that start with certain prefixes
    ...Object.fromEntries(Object.entries(process.env)),
  },
});
