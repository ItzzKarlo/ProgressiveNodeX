@echo off
setlocal EnableExtensions

set "DEFAULT_ROOT=M:\_Development\_Projects\PNX\ProgressiveNodeX-CLI\src\templates\apps"
set "ROOT_ARG="
set "PNX_OVERWRITE=0"

:parse_args
if "%~1"=="" goto args_done

if /I "%~1"=="--force" (
    set "PNX_OVERWRITE=1"
) else (
    set "ROOT_ARG=%~1"
)

shift
goto parse_args

:args_done

if defined ROOT_ARG (
    set "PNX_TEMPLATE_ROOT=%ROOT_ARG%"
) else (
    set "PNX_TEMPLATE_ROOT=%DEFAULT_ROOT%"
    if exist "%CD%\flask\" set "PNX_TEMPLATE_ROOT=%CD%"
    if exist "%CD%\fastapi\" set "PNX_TEMPLATE_ROOT=%CD%"
    if exist "%CD%\vue\" set "PNX_TEMPLATE_ROOT=%CD%"
    if exist "%CD%\cs-desktop\" set "PNX_TEMPLATE_ROOT=%CD%"
)

set "PNX_SELF=%~f0"

echo.
echo ProgressiveNodeX template generator
echo Target: %PNX_TEMPLATE_ROOT%
if "%PNX_OVERWRITE%"=="1" (
    echo Mode: overwrite existing files
) else (
    echo Mode: skip existing files
)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { $raw = [System.IO.File]::ReadAllText($env:PNX_SELF); $marker = '# POWERSHELL_PAYLOAD'; $i = $raw.LastIndexOf($marker); if ($i -lt 0) { throw 'Payload marker not found.' }; $code = $raw.Substring($i + $marker.Length); Invoke-Expression $code; exit 0 } catch { Write-Error $_; exit 1 }"

set "PNX_EXIT=%ERRORLEVEL%"

if not "%PNX_EXIT%"=="0" (
    echo.
    echo Failed.
    exit /b %PNX_EXIT%
)

echo.
echo Done.
exit /b 0

# POWERSHELL_PAYLOAD

$ErrorActionPreference = "Stop"

$Root = $env:PNX_TEMPLATE_ROOT
$Overwrite = $env:PNX_OVERWRITE -eq "1"

New-Item -ItemType Directory -Force -Path $Root | Out-Null

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$CreatedTemplates = New-Object System.Collections.Generic.List[string]
$WrittenFiles = 0
$SkippedFiles = 0

function Write-TemplateFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    if ((Test-Path -LiteralPath $Path) -and -not $Overwrite) {
        Write-Host "  skip  $Path"
        $script:SkippedFiles++
        return
    }

    $text = $Content.TrimStart("`r", "`n")
    [System.IO.File]::WriteAllText($Path, $text, $utf8NoBom)

    Write-Host "  write $Path"
    $script:WrittenFiles++
}

function Convert-ToPrettyJson {
    param([object]$Value)

    return (($Value | ConvertTo-Json -Depth 32) + "`n")
}

function Add-PnxTemplate {
    param(
        [string]$Name,
        [string]$DisplayName,
        [string]$Description,
        [string]$Language,
        [string[]]$Tags,
        [System.Collections.IDictionary]$Scripts,
        [System.Collections.IDictionary]$Files
    )

    $dir = Join-Path $Root $Name
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    Write-Host ""
    Write-Host "Creating template: $Name"

    $templateJson = [ordered]@{
        name = $Name
        display_name = $DisplayName
        description = $Description
        language = $Language
        version = "1.0.0"
        type = "app"
        tags = $Tags
        scripts = $Scripts
    }

    $pnxJson = [ordered]@{
        name = $Name
        version = "0.1.0"
        type = "app"
        template = $Name
        scripts = $Scripts
        commands = $Scripts
    }

    Write-TemplateFile -Path (Join-Path $dir "pnx.template.json") -Content (Convert-ToPrettyJson $templateJson)
    Write-TemplateFile -Path (Join-Path $dir "pnx.json") -Content (Convert-ToPrettyJson $pnxJson)

    if (-not $Files.Contains("README.md")) {
        $readme = @"
# $DisplayName

$Description

## Quick start

Use the commands from `pnx.json`, or run the project manually with the native tooling for this stack.
"@
        Write-TemplateFile -Path (Join-Path $dir "README.md") -Content $readme
    }

    foreach ($rel in $Files.Keys) {
        Write-TemplateFile -Path (Join-Path $dir $rel) -Content $Files[$rel]
    }

    $CreatedTemplates.Add($Name) | Out-Null
}

Add-PnxTemplate `
    -Name "react-vite" `
    -DisplayName "React Vite" `
    -Description "A modern React single-page application powered by Vite." `
    -Language "JavaScript" `
    -Tags @("react", "vite", "frontend", "spa") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run dev"
        build = "npm run build"
        preview = "npm run preview"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "react-vite-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {}
}
'@
        "index.html" = @'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React Vite App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'@
        "src/main.jsx" = @'
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'@
        "src/App.jsx" = @'
export default function App() {
  return (
    <main className="page">
      <section className="card">
        <p className="eyebrow">ProgressiveNodeX</p>
        <h1>React + Vite</h1>
        <p>
          Your app template is ready. Start editing <code>src/App.jsx</code>.
        </p>
      </section>
    </main>
  );
}
'@
        "src/App.css" = @'
body {
  margin: 0;
  font-family: Inter, system-ui, Arial, sans-serif;
  background: #0f172a;
  color: #e5e7eb;
}

.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

.card {
  max-width: 720px;
  padding: 48px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.eyebrow {
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.8rem;
}
'@
        ".gitignore" = @'
node_modules
dist
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "nextjs" `
    -DisplayName "Next.js" `
    -Description "A Next.js app router starter for full-stack React applications." `
    -Language "JavaScript" `
    -Tags @("nextjs", "react", "frontend", "fullstack") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run dev"
        build = "npm run build"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "nextjs-app",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {}
}
'@
        "app/layout.jsx" = @'
import "./globals.css";

export const metadata = {
  title: "Next.js App",
  description: "Generated by ProgressiveNodeX"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
'@
        "app/page.jsx" = @'
export default function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <span>ProgressiveNodeX</span>
        <h1>Next.js starter</h1>
        <p>Edit <code>app/page.jsx</code> and build something awesome.</p>
      </section>
    </main>
  );
}
'@
        "app/globals.css" = @'
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, system-ui, Arial, sans-serif;
  background: #020617;
  color: #f8fafc;
}

.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
}

.hero {
  max-width: 760px;
}

.hero span {
  color: #22c55e;
  font-weight: 700;
}

.hero h1 {
  font-size: clamp(3rem, 10vw, 7rem);
  margin: 12px 0;
}
'@
        ".gitignore" = @'
node_modules
.next
out
.env
.env.local
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "sveltekit" `
    -DisplayName "SvelteKit" `
    -Description "A SvelteKit application starter with Vite." `
    -Language "JavaScript" `
    -Tags @("svelte", "sveltekit", "vite", "frontend") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run dev"
        build = "npm run build"
        preview = "npm run preview"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "sveltekit-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@sveltejs/kit": "latest",
    "@sveltejs/adapter-auto": "latest",
    "svelte": "latest",
    "vite": "latest"
  },
  "devDependencies": {}
}
'@
        "svelte.config.js" = @'
import adapter from "@sveltejs/adapter-auto";

export default {
  kit: {
    adapter: adapter()
  }
};
'@
        "vite.config.js" = @'
import { sveltekit } from "@sveltejs/kit/vite";

export default {
  plugins: [sveltekit()]
};
'@
        "src/app.html" = @'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    %sveltekit.head%
  </head>
  <body>
    <div>%sveltekit.body%</div>
  </body>
</html>
'@
        "src/routes/+page.svelte" = @'
<script>
  const name = "SvelteKit";
</script>

<main>
  <p>ProgressiveNodeX</p>
  <h1>{name} starter</h1>
  <span>Edit <code>src/routes/+page.svelte</code>.</span>
</main>

<style>
  main {
    min-height: 100vh;
    display: grid;
    place-content: center;
    gap: 12px;
    font-family: Inter, system-ui, Arial, sans-serif;
    background: #0f172a;
    color: white;
  }

  h1 {
    font-size: clamp(3rem, 8vw, 6rem);
    margin: 0;
  }

  p {
    color: #fb7185;
    font-weight: 700;
  }
</style>
'@
        ".gitignore" = @'
node_modules
.svelte-kit
build
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "angular" `
    -DisplayName "Angular" `
    -Description "A minimal Angular single-page application starter." `
    -Language "TypeScript" `
    -Tags @("angular", "typescript", "frontend", "spa") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm start"
        build = "npm run build"
        test = "npm test"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "angular-app",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "start": "ng serve",
    "build": "ng build",
    "test": "ng test"
  },
  "dependencies": {
    "@angular/animations": "latest",
    "@angular/common": "latest",
    "@angular/compiler": "latest",
    "@angular/core": "latest",
    "@angular/forms": "latest",
    "@angular/platform-browser": "latest",
    "@angular/router": "latest",
    "rxjs": "latest",
    "tslib": "latest",
    "zone.js": "latest"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "latest",
    "@angular/cli": "latest",
    "@angular/compiler-cli": "latest",
    "typescript": "latest"
  }
}
'@
        "angular.json" = @'
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "projects": {
    "angular-app": {
      "projectType": "application",
      "sourceRoot": "src",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/angular-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "tsConfig": "tsconfig.app.json",
            "styles": ["src/styles.css"]
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "options": {
            "buildTarget": "angular-app:build"
          }
        }
      }
    }
  }
}
'@
        "tsconfig.json" = @'
{
  "compileOnSave": false,
  "compilerOptions": {
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "experimentalDecorators": true,
    "moduleResolution": "bundler",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022"
  }
}
'@
        "tsconfig.app.json" = @'
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"]
}
'@
        "src/index.html" = @'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Angular App</title>
    <base href="/">
    <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body>
    <app-root></app-root>
  </body>
</html>
'@
        "src/main.ts" = @'
import { bootstrapApplication } from "@angular/platform-browser";
import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  standalone: true,
  template: `
    <main>
      <p>ProgressiveNodeX</p>
      <h1>Angular starter</h1>
      <span>Edit <code>src/main.ts</code>.</span>
    </main>
  `
})
class AppComponent {}

bootstrapApplication(AppComponent).catch((error) => console.error(error));
'@
        "src/styles.css" = @'
body {
  margin: 0;
  font-family: Inter, system-ui, Arial, sans-serif;
  background: #111827;
  color: #f9fafb;
}

main {
  min-height: 100vh;
  display: grid;
  place-content: center;
  text-align: center;
}

p {
  color: #f97316;
  font-weight: 700;
}

h1 {
  font-size: clamp(3rem, 8vw, 6rem);
  margin: 0;
}
'@
        ".gitignore" = @'
node_modules
dist
.angular
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "astro" `
    -DisplayName "Astro" `
    -Description "A content-friendly Astro website starter." `
    -Language "JavaScript" `
    -Tags @("astro", "frontend", "static-site", "content") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run dev"
        build = "npm run build"
        preview = "npm run preview"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "astro-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "latest"
  },
  "devDependencies": {}
}
'@
        "astro.config.mjs" = @'
import { defineConfig } from "astro/config";

export default defineConfig({});
'@
        "src/pages/index.astro" = @'
---
import "../styles/global.css";
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Astro App</title>
    <meta name="viewport" content="width=device-width" />
  </head>
  <body>
    <main>
      <p>ProgressiveNodeX</p>
      <h1>Astro starter</h1>
      <span>Edit <code>src/pages/index.astro</code>.</span>
    </main>
  </body>
</html>
'@
        "src/styles/global.css" = @'
body {
  margin: 0;
  font-family: Inter, system-ui, Arial, sans-serif;
  background: #0c0a09;
  color: #fafaf9;
}

main {
  min-height: 100vh;
  display: grid;
  place-content: center;
  text-align: center;
}

p {
  color: #a78bfa;
  font-weight: 700;
}

h1 {
  font-size: clamp(3rem, 8vw, 6rem);
  margin: 0;
}
'@
        ".gitignore" = @'
node_modules
dist
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "express-api" `
    -DisplayName "Express API" `
    -Description "A lightweight Node.js REST API starter using Express." `
    -Language "JavaScript" `
    -Tags @("node", "express", "api", "backend") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run dev"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "express-api",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "node --watch src/index.js",
    "start": "node src/index.js"
  },
  "dependencies": {
    "cors": "latest",
    "dotenv": "latest",
    "express": "latest",
    "morgan": "latest"
  },
  "devDependencies": {}
}
'@
        "src/index.js" = @'
import "dotenv/config";
import express from "express";
import cors from "cors";
import morgan from "morgan";

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(morgan("dev"));
app.use(express.json());

app.get("/", (_request, response) => {
  response.json({
    name: "express-api",
    status: "ok",
    generatedBy: "ProgressiveNodeX"
  });
});

app.get("/health", (_request, response) => {
  response.json({ ok: true });
});

app.listen(port, () => {
  console.log(`Express API running on http://localhost:${port}`);
});
'@
        ".env.example" = @'
PORT=3000
'@
        ".gitignore" = @'
node_modules
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "nestjs-api" `
    -DisplayName "NestJS API" `
    -Description "A structured Node.js API starter using NestJS and TypeScript." `
    -Language "TypeScript" `
    -Tags @("node", "nestjs", "api", "backend", "typescript") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run start:dev"
        build = "npm run build"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "nestjs-api",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "start": "node dist/main.js",
    "start:dev": "nest start --watch",
    "build": "nest build"
  },
  "dependencies": {
    "@nestjs/common": "latest",
    "@nestjs/core": "latest",
    "@nestjs/platform-express": "latest",
    "reflect-metadata": "latest",
    "rxjs": "latest"
  },
  "devDependencies": {
    "@nestjs/cli": "latest",
    "@nestjs/schematics": "latest",
    "@nestjs/testing": "latest",
    "@types/node": "latest",
    "typescript": "latest"
  }
}
'@
        "tsconfig.json" = @'
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strict": true
  }
}
'@
        "src/main.ts" = @'
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const port = process.env.PORT || 3000;

  await app.listen(port);
  console.log(`NestJS API running on http://localhost:${port}`);
}

bootstrap();
'@
        "src/app.module.ts" = @'
import { Module } from "@nestjs/common";
import { AppController } from "./app.controller";

@Module({
  imports: [],
  controllers: [AppController],
  providers: []
})
export class AppModule {}
'@
        "src/app.controller.ts" = @'
import { Controller, Get } from "@nestjs/common";

@Controller()
export class AppController {
  @Get()
  index() {
    return {
      name: "nestjs-api",
      status: "ok",
      generatedBy: "ProgressiveNodeX"
    };
  }

  @Get("health")
  health() {
    return { ok: true };
  }
}
'@
        ".gitignore" = @'
node_modules
dist
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "node-cli" `
    -DisplayName "Node CLI" `
    -Description "A small Node.js command-line application starter." `
    -Language "JavaScript" `
    -Tags @("node", "cli", "tooling") `
    -Scripts ([ordered]@{
        install = "npm install"
        run = "npm start"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "node-cli",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "bin": {
    "node-cli": "./src/index.js"
  },
  "scripts": {
    "start": "node src/index.js"
  },
  "dependencies": {
    "commander": "latest"
  },
  "devDependencies": {}
}
'@
        "src/index.js" = @'
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
'@
        ".gitignore" = @'
node_modules
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "python-cli" `
    -DisplayName "Python CLI" `
    -Description "A Python command-line application starter." `
    -Language "Python" `
    -Tags @("python", "cli", "tooling") `
    -Scripts ([ordered]@{
        install = "pip install -e ."
        run = "python -m app"
        start = "python -m app"
    }) `
    -Files ([ordered]@{
        "pyproject.toml" = @'
[project]
name = "python-cli"
version = "0.1.0"
description = "A ProgressiveNodeX generated Python CLI"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
python-cli = "app.main:main"

[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"
'@
        "src/app/__init__.py" = @'
__all__ = ["main"]
'@
        "src/app/__main__.py" = @'
from .main import main

if __name__ == "__main__":
    main()
'@
        "src/app/main.py" = @'
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="A ProgressiveNodeX generated Python CLI.")
    parser.add_argument("--name", default="PNX", help="Name to greet.")
    args = parser.parse_args()

    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
'@
        ".gitignore" = @'
__pycache__/
*.pyc
.venv/
dist/
build/
*.egg-info/
.env
'@
    })

Add-PnxTemplate `
    -Name "django" `
    -DisplayName "Django" `
    -Description "A minimal Django web application starter." `
    -Language "Python" `
    -Tags @("python", "django", "web", "backend") `
    -Scripts ([ordered]@{
        install = "pip install -r requirements.txt"
        dev = "python manage.py runserver"
        migrate = "python manage.py migrate"
        start = "python manage.py runserver"
    }) `
    -Files ([ordered]@{
        "requirements.txt" = @'
Django
'@
        "manage.py" = @'
#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
'@
        "config/__init__.py" = @'
'@
        "config/settings.py" = @'
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only-change-me"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
'@
        "config/urls.py" = @'
from django.contrib import admin
from django.urls import path

from app.views import home

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
]
'@
        "config/wsgi.py" = @'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
'@
        "config/asgi.py" = @'
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
'@
        "app/__init__.py" = @'
'@
        "app/views.py" = @'
from django.http import JsonResponse


def home(_request):
    return JsonResponse({
        "name": "django",
        "status": "ok",
        "generated_by": "ProgressiveNodeX",
    })
'@
        ".gitignore" = @'
__pycache__/
*.pyc
.venv/
db.sqlite3
.env
'@
    })

Add-PnxTemplate `
    -Name "streamlit" `
    -DisplayName "Streamlit" `
    -Description "A quick Python data app starter using Streamlit." `
    -Language "Python" `
    -Tags @("python", "streamlit", "data", "dashboard") `
    -Scripts ([ordered]@{
        install = "pip install -r requirements.txt"
        dev = "streamlit run app.py"
        start = "streamlit run app.py"
    }) `
    -Files ([ordered]@{
        "requirements.txt" = @'
streamlit
pandas
'@
        "app.py" = @'
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Streamlit App", page_icon="🚀")

st.title("ProgressiveNodeX Streamlit starter")
st.write("Edit `app.py` to build your dashboard.")

data = pd.DataFrame(
    {
        "name": ["PNX", "Template", "App"],
        "value": [100, 75, 50],
    }
)

st.bar_chart(data, x="name", y="value")
'@
        ".gitignore" = @'
__pycache__/
*.pyc
.venv/
.env
'@
    })

Add-PnxTemplate `
    -Name "go-api" `
    -DisplayName "Go API" `
    -Description "A small Go HTTP API starter." `
    -Language "Go" `
    -Tags @("go", "api", "backend") `
    -Scripts ([ordered]@{
        dev = "go run ."
        build = "go build -o app.exe ."
        start = "go run ."
    }) `
    -Files ([ordered]@{
        "go.mod" = @'
module go-api

go 1.22
'@
        "main.go" = @'
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000"
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, map[string]any{
			"name":        "go-api",
			"status":      "ok",
			"generatedBy": "ProgressiveNodeX",
		})
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, map[string]any{"ok": true})
	})

	log.Printf("Go API running on http://localhost:%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func writeJSON(w http.ResponseWriter, payload any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(payload)
}
'@
        ".gitignore" = @'
bin/
dist/
*.exe
.env
'@
    })

Add-PnxTemplate `
    -Name "rust-cli" `
    -DisplayName "Rust CLI" `
    -Description "A simple Rust command-line application starter." `
    -Language "Rust" `
    -Tags @("rust", "cli", "systems") `
    -Scripts ([ordered]@{
        dev = "cargo run"
        build = "cargo build --release"
        start = "cargo run"
    }) `
    -Files ([ordered]@{
        "Cargo.toml" = @'
[package]
name = "rust-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
'@
        "src/main.rs" = @'
fn main() {
    println!("Hello from your ProgressiveNodeX Rust CLI.");
}
'@
        ".gitignore" = @'
target/
Cargo.lock
.env
'@
    })

Add-PnxTemplate `
    -Name "dotnet-webapi" `
    -DisplayName ".NET Web API" `
    -Description "A minimal ASP.NET Core Web API starter." `
    -Language "C#" `
    -Tags @("dotnet", "csharp", "api", "backend") `
    -Scripts ([ordered]@{
        restore = "dotnet restore"
        dev = "dotnet run"
        build = "dotnet build"
        start = "dotnet run"
    }) `
    -Files ([ordered]@{
        "DotnetWebApi.csproj" = @'
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

</Project>
'@
        "Program.cs" = @'
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => new
{
    name = "dotnet-webapi",
    status = "ok",
    generatedBy = "ProgressiveNodeX"
});

app.MapGet("/health", () => new { ok = true });

app.Run();
'@
        "appsettings.json" = @'
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
'@
        ".gitignore" = @'
bin/
obj/
.vs/
.env
'@
    })

Add-PnxTemplate `
    -Name "java-springboot" `
    -DisplayName "Java Spring Boot" `
    -Description "A Java Spring Boot REST API starter." `
    -Language "Java" `
    -Tags @("java", "springboot", "api", "backend") `
    -Scripts ([ordered]@{
        dev = "mvn spring-boot:run"
        build = "mvn package"
        start = "mvn spring-boot:run"
    }) `
    -Files ([ordered]@{
        "pom.xml" = @'
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.pnx</groupId>
  <artifactId>java-springboot</artifactId>
  <version>0.1.0</version>

  <properties>
    <java.version>21</java.version>
    <spring-boot.version>3.3.0</spring-boot.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>${spring-boot.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-maven-plugin</artifactId>
        <version>${spring-boot.version}</version>
      </plugin>
    </plugins>
  </build>
</project>
'@
        "src/main/java/com/pnx/demo/DemoApplication.java" = @'
package com.pnx.demo;

import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @GetMapping("/")
    public Map<String, Object> index() {
        return Map.of(
            "name", "java-springboot",
            "status", "ok",
            "generatedBy", "ProgressiveNodeX"
        );
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of("ok", true);
    }
}
'@
        "src/main/resources/application.properties" = @'
server.port=3000
'@
        ".gitignore" = @'
target/
.env
.idea/
*.iml
'@
    })

Add-PnxTemplate `
    -Name "php-api" `
    -DisplayName "PHP API" `
    -Description "A small dependency-light PHP API starter." `
    -Language "PHP" `
    -Tags @("php", "api", "backend") `
    -Scripts ([ordered]@{
        dev = "php -S localhost:3000 -t public"
        start = "php -S localhost:3000 -t public"
    }) `
    -Files ([ordered]@{
        "composer.json" = @'
{
  "name": "pnx/php-api",
  "description": "A ProgressiveNodeX generated PHP API",
  "type": "project",
  "require": {
    "php": ">=8.2"
  },
  "scripts": {
    "start": "php -S localhost:3000 -t public"
  }
}
'@
        "public/index.php" = @'
<?php

declare(strict_types=1);

header("Content-Type: application/json");

$path = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);

if ($path === "/health") {
    echo json_encode(["ok" => true]);
    exit;
}

echo json_encode([
    "name" => "php-api",
    "status" => "ok",
    "generatedBy" => "ProgressiveNodeX"
]);
'@
        ".gitignore" = @'
vendor/
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "electron" `
    -DisplayName "Electron" `
    -Description "A desktop application starter using Electron." `
    -Language "JavaScript" `
    -Tags @("electron", "desktop", "javascript") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm start"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "electron-app",
  "private": true,
  "version": "0.1.0",
  "main": "main.js",
  "scripts": {
    "start": "electron ."
  },
  "dependencies": {
    "electron": "latest"
  },
  "devDependencies": {}
}
'@
        "main.js" = @'
const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const window = new BrowserWindow({
    width: 1100,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  window.loadFile("renderer/index.html");
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
'@
        "preload.js" = @'
window.addEventListener("DOMContentLoaded", () => {
  console.log("Electron app loaded.");
});
'@
        "renderer/index.html" = @'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Electron App</title>
    <link rel="stylesheet" href="./style.css" />
  </head>
  <body>
    <main>
      <p>ProgressiveNodeX</p>
      <h1>Electron starter</h1>
      <span>Edit <code>renderer/index.html</code>.</span>
    </main>
    <script src="./app.js"></script>
  </body>
</html>
'@
        "renderer/app.js" = @'
console.log("Hello from Electron renderer.");
'@
        "renderer/style.css" = @'
body {
  margin: 0;
  font-family: Inter, system-ui, Arial, sans-serif;
  background: #111827;
  color: white;
}

main {
  min-height: 100vh;
  display: grid;
  place-content: center;
  text-align: center;
}

p {
  color: #38bdf8;
  font-weight: 700;
}

h1 {
  font-size: clamp(3rem, 8vw, 6rem);
  margin: 0;
}
'@
        ".gitignore" = @'
node_modules
dist
out
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "tauri" `
    -DisplayName "Tauri" `
    -Description "A lightweight desktop application starter using Tauri." `
    -Language "Rust/JavaScript" `
    -Tags @("tauri", "desktop", "rust", "javascript") `
    -Scripts ([ordered]@{
        install = "npm install"
        dev = "npm run tauri dev"
        build = "npm run tauri build"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "tauri-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "tauri": "tauri"
  },
  "dependencies": {
    "@tauri-apps/cli": "latest"
  },
  "devDependencies": {}
}
'@
        "index.html" = @'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Tauri App</title>
    <script type="module" src="/src/main.js"></script>
    <style>
      body {
        margin: 0;
        font-family: Inter, system-ui, Arial, sans-serif;
        background: #09090b;
        color: white;
      }

      main {
        min-height: 100vh;
        display: grid;
        place-content: center;
        text-align: center;
      }

      p {
        color: #facc15;
        font-weight: 700;
      }

      h1 {
        font-size: clamp(3rem, 8vw, 6rem);
        margin: 0;
      }
    </style>
  </head>
  <body>
    <main>
      <p>ProgressiveNodeX</p>
      <h1>Tauri starter</h1>
      <span>Edit <code>index.html</code>.</span>
    </main>
  </body>
</html>
'@
        "src/main.js" = @'
console.log("Hello from Tauri.");
'@
        "src-tauri/Cargo.toml" = @'
[package]
name = "tauri_app"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2", features = [] }

[build-dependencies]
tauri-build = { version = "2", features = [] }
'@
        "src-tauri/build.rs" = @'
fn main() {
    tauri_build::build()
}
'@
        "src-tauri/src/main.rs" = @'
fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
'@
        "src-tauri/tauri.conf.json" = @'
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "Tauri App",
  "version": "0.1.0",
  "identifier": "com.pnx.tauriapp",
  "build": {
    "beforeDevCommand": "",
    "beforeBuildCommand": "",
    "frontendDist": "../",
    "devUrl": "http://localhost:1420"
  },
  "app": {
    "windows": [
      {
        "title": "Tauri App",
        "width": 1100,
        "height": 720
      }
    ]
  },
  "bundle": {
    "active": true,
    "targets": "all"
  }
}
'@
        ".gitignore" = @'
node_modules
src-tauri/target
dist
.env
.DS_Store
'@
    })

Add-PnxTemplate `
    -Name "flutter" `
    -DisplayName "Flutter" `
    -Description "A cross-platform Flutter application starter." `
    -Language "Dart" `
    -Tags @("flutter", "dart", "mobile", "desktop", "cross-platform") `
    -Scripts ([ordered]@{
        get = "flutter pub get"
        dev = "flutter run"
        build = "flutter build"
        start = "flutter run"
    }) `
    -Files ([ordered]@{
        "pubspec.yaml" = @'
name: flutter_app
description: A ProgressiveNodeX generated Flutter application.
publish_to: "none"
version: 0.1.0+1

environment:
  sdk: ">=3.4.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter

flutter:
  uses-material-design: true
'@
        "lib/main.dart" = @'
import "package:flutter/material.dart";

void main() {
  runApp(const PnxApp());
}

class PnxApp extends StatelessWidget {
  const PnxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Flutter App",
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text(
          "ProgressiveNodeX Flutter starter",
          style: Theme.of(context).textTheme.headlineMedium,
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
'@
        ".gitignore" = @'
.dart_tool/
.packages
build/
.pub-cache/
.env
'@
    })

Add-PnxTemplate `
    -Name "react-native" `
    -DisplayName "React Native" `
    -Description "A React Native mobile application starter." `
    -Language "JavaScript" `
    -Tags @("react-native", "mobile", "react", "javascript") `
    -Scripts ([ordered]@{
        install = "npm install"
        android = "npm run android"
        ios = "npm run ios"
        start = "npm start"
    }) `
    -Files ([ordered]@{
        "package.json" = @'
{
  "name": "ReactNativeApp",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "start": "react-native start"
  },
  "dependencies": {
    "@react-native-community/cli": "latest",
    "react": "latest",
    "react-native": "latest"
  },
  "devDependencies": {}
}
'@
        "app.json" = @'
{
  "name": "ReactNativeApp",
  "displayName": "React Native App"
}
'@
        "index.js" = @'
import { AppRegistry } from "react-native";
import App from "./App";
import { name as appName } from "./app.json";

AppRegistry.registerComponent(appName, () => App);
'@
        "App.jsx" = @'
import React from "react";
import { SafeAreaView, StyleSheet, Text } from "react-native";

export default function App() {
  return (
    <SafeAreaView style={styles.page}>
      <Text style={styles.kicker}>ProgressiveNodeX</Text>
      <Text style={styles.title}>React Native starter</Text>
      <Text style={styles.body}>Edit App.jsx to build your mobile app.</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    backgroundColor: "#0f172a"
  },
  kicker: {
    color: "#38bdf8",
    fontWeight: "700",
    marginBottom: 12
  },
  title: {
    color: "white",
    fontSize: 36,
    fontWeight: "800",
    textAlign: "center"
  },
  body: {
    color: "#cbd5e1",
    marginTop: 12,
    textAlign: "center"
  }
});
'@
        ".gitignore" = @'
node_modules
android/.gradle
android/app/build
ios/Pods
.env
.DS_Store
'@
    })

Write-Host ""
Write-Host "Summary"
Write-Host "-------"
Write-Host "Templates touched: $($CreatedTemplates.Count)"
Write-Host "Files written:     $WrittenFiles"
Write-Host "Files skipped:     $SkippedFiles"
Write-Host ""
Write-Host "Template root:"
Write-Host $Root