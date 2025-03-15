CREATE TABLE `questions` (
	`id` integer PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`question` text NOT NULL,
	`subjectId` integer,
	`created_at` integer DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` integer DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`subjectId`) REFERENCES `subjects`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `questions_subject_idx` ON `questions` (`subjectId`);--> statement-breakpoint
CREATE INDEX `questions_title_idx` ON `questions` (`title`);--> statement-breakpoint
CREATE TABLE `subjects` (
	`id` integer PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`description` text,
	`created_at` integer DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updated_at` integer DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE INDEX `subjects_name_idx` ON `subjects` (`name`);