import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe, Logger } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  const app = await NestFactory.create(AppModule);

  const port = process.env.PORT || 4000;

  // Configure Validation Pipe for DTO validation
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: true,
    }),
  );

  // Configure Swagger Document
  const config = new DocumentBuilder()
    .setTitle('DevForge NestJS API')
    .setDescription('The DevForge NestJS application developer API endpoint definitions')
    .setVersion('1.0')
    .addTag('api')
    .addTag('health')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('swagger', app, document);

  await app.listen(port);
  logger.log(`NestJS server successfully started on http://localhost:${port}`);
  logger.log(`Swagger documentation available at http://localhost:${port}/swagger`);
  logger.log(`Debug inspector available (if run with debug) on port 9229`);
}
bootstrap();
