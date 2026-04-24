import { Module } from '@nestjs/common';
import { AppController } from './controllers/app.controller';
import { AppService } from './services/app.service';
import { DatabaseService } from './database/database.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService, DatabaseService],
})
export class AppModule {}
