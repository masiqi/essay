import { Hono } from 'hono';
import { initDbConnect } from '../db/database';
import { subjects } from '../db/schema';
import { eq } from 'drizzle-orm';

export type Env = {
  DB: D1Database;
};

const subject = new Hono<{ Bindings: Env }>();

// 获取所有科目
subject.get('/', async (c) => {
  const db = initDbConnect(c.env.DB);
  try {
    const subjectsList = await db.select().from(subjects).execute();
    return c.json({
      status: 0,
      msg: 'ok',
      data: subjectsList
    });
  } catch (error) {
    console.error("Error fetching subjects:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 获取单个科目
subject.get('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  try {
    const subject = await db.select().from(subjects).where(eq(subjects.id, id)).get();
    if (!subject) {
      return c.json({
        status: 404,
        msg: "Subject not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: subject
    });
  } catch (error) {
    console.error("Error fetching subject:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 创建科目
subject.post('/', async (c) => {
  const db = initDbConnect(c.env.DB);
  const body = await c.req.json();
  try {
    const newSubject = await db.insert(subjects).values({
      name: body.name,
      description: body.description || null
    }).returning().execute();
    return c.json({
      status: 0,
      msg: 'ok',
      data: newSubject[0]
    });
  } catch (error) {
    console.error("Error creating subject:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 更新科目
subject.put('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  const body = await c.req.json();
  try {
    const updatedSubject = await db.update(subjects).set({
      name: body.name,
      description: body.description
    }).where(eq(subjects.id, id)).returning().execute();
    if (!updatedSubject.length) {
      return c.json({
        status: 404,
        msg: "Subject not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: updatedSubject[0]
    });
  } catch (error) {
    console.error("Error updating subject:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 删除科目
subject.delete('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  try {
    const deletedSubject = await db.delete(subjects).where(eq(subjects.id, id)).returning().execute();
    if (!deletedSubject.length) {
      return c.json({
        status: 404,
        msg: "Subject not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: null
    });
  } catch (error) {
    console.error("Error deleting subject:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

export { subject };
