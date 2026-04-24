import { Injectable, OnModuleDestroy, OnModuleInit, InternalServerErrorException } from '@nestjs/common';
import { Client } from 'pg';

@Injectable()
export class DatabaseService implements OnModuleInit, OnModuleDestroy {
  private client: Client;

  constructor() {
    this.client = new Client({
      host: process.env.DB_HOST || 'app-postgres',
      port: parseInt(process.env.DB_PORT || '5432', 10),
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'password',
      database: process.env.DB_NAME || 'postgres',
    });
  }

  async onModuleInit() {
    try {
      await this.client.connect();
    } catch (error) {
      console.error('Failed to connect to the database on init', error);
    }
  }

  async onModuleDestroy() {
    await this.client.end();
  }

  async checkConnection(): Promise<any[]> {
    try {
      const res = await this.client.query('SELECT 1 as result');
      return res.rows;
    } catch (error) {
      throw new InternalServerErrorException('Database connection failed: ' + error.message);
    }
  }
}
