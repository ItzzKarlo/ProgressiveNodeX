#!/usr/bin/env node

import { Command } from "commander";

const program = new Command();

program
  .name("node-cli")
  .description("A ProgressiveNodeX generated CLI")
  .version("0.1.0");

program
  .command("hello")
  .description("Print a hello message")
  .action(() => {
    console.log("Hello from your Node CLI.");
  });

program.parse(process.argv);

if (!process.argv.slice(2).length) {
  program.help();
}