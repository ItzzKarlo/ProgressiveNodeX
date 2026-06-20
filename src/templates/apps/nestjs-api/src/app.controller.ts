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