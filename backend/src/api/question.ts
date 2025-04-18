import { Hono } from 'hono';
import { initDbConnect } from '../db/database';
import { questions } from '../db/schema';
import { eq } from 'drizzle-orm';

export type Env = {
  DB: D1Database;
};

const question = new Hono<{ Bindings: Env }>();

// 获取所有题目
question.get('/', async (c) => {
  const db = initDbConnect(c.env.DB);
  const subjectId = c.req.query('subjectId');
  try {
    let questionsList;
    if (subjectId) {
      questionsList = await db.select().from(questions).where(eq(questions.subjectId, Number(subjectId))).execute();
    } else {
      questionsList = await db.select().from(questions).execute();
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: questionsList
    });
  } catch (error) {
    console.error("Error fetching questions:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 获取单个题目
question.get('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  try {
    const question = await db.select().from(questions).where(eq(questions.id, id)).get();
    if (!question) {
      return c.json({
        status: 404,
        msg: "Question not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: question
    });
  } catch (error) {
    console.error("Error fetching question:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 创建题目
question.post('/', async (c) => {
  const db = initDbConnect(c.env.DB);
  const body = await c.req.json();
  try {
    const newQuestion = await db.insert(questions).values({
      id: body.id,
      title: body.title,
      question: body.question,
      subjectId: body.subjectId,
    }).returning().execute();
    return c.json({
      status: 0,
      msg: 'ok',
      data: newQuestion[0]
    });
  } catch (error) {
    console.error("Error creating question:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 更新题目
question.put('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  const body = await c.req.json();
  try {
    const updatedQuestion = await db.update(questions).set({
      title: body.title,
      question: body.question,
      subjectId: body.subjectId,
    }).where(eq(questions.id, id)).returning().execute();
    if (!updatedQuestion.length) {
      return c.json({
        status: 404,
        msg: "Question not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: updatedQuestion[0]
    });
  } catch (error) {
    console.error("Error updating question:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

// 删除题目
question.delete('/:id', async (c) => {
  const db = initDbConnect(c.env.DB);
  const id = Number(c.req.param('id'));
  try {
    const deletedQuestion = await db.delete(questions).where(eq(questions.id, id)).returning().execute();
    if (!deletedQuestion.length) {
      return c.json({
        status: 404,
        msg: "Question not found",
        data: null
      }, 404);
    }
    return c.json({
      status: 0,
      msg: 'ok',
      data: null
    });
  } catch (error) {
    console.error("Error deleting question:", error);
    return c.json({
      status: 500,
      msg: "Internal server error",
      data: null
    }, 500);
  }
});

export { question };
