import { sql } from 'drizzle-orm';
import { sqliteTable, text, integer, index, uniqueIndex, primaryKey } from 'drizzle-orm/sqlite-core';

export const subjects = sqliteTable('subjects', {
  id: integer('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  created_at: integer('created_at', { mode: 'timestamp' }).notNull().default(sql`CURRENT_TIMESTAMP`),
  updated_at: integer('updated_at', { mode: 'timestamp' }).notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => {
  return {
    pk: primaryKey({ columns: [table.id] }),
    nameIdx: index('subjects_name_idx').on(table.name),
  }
});

export const questions = sqliteTable('questions', {
  id: integer('id').notNull(),
  title: text('title').notNull(),
  question: text('question').notNull(),
  subjectId: integer('subjectId').references(() => subjects.id),
  created_at: integer('created_at', { mode: 'timestamp' }).notNull().default(sql`CURRENT_TIMESTAMP`),
  updated_at: integer('updated_at', { mode: 'timestamp' }).notNull().default(sql`CURRENT_TIMESTAMP`),
}, (table) => {
  return {
    pk: primaryKey({ columns: [table.id] }),
    subjectIdx: index('questions_subject_idx').on(table.subjectId),
    titleIdx: index('questions_title_idx').on(table.title),
  }
});
