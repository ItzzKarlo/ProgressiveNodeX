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