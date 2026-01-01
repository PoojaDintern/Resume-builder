USE [resume_builder]
GO
/****** Object:  Table [dbo].[Certifications]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Certifications](
	[CertificationID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[CertificationName] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[CertificationID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Education]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Education](
	[EducationID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[College] [varchar](100) NULL,
	[University] [varchar](100) NULL,
	[Course] [varchar](50) NULL,
	[Year] [int] NULL,
	[CGPA] [decimal](4, 2) NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[EducationID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Interests]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Interests](
	[InterestID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[InterestName] [varchar](100) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[InterestID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PersonalInformation]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PersonalInformation](
	[PersonalInfoID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[FullName] [varchar](100) NULL,
	[Email] [varchar](100) NULL,
	[PhoneNumber] [varchar](30) NULL,
	[DateOfBirth] [date] NULL,
	[Location] [varchar](100) NULL,
	[PhotoPath] [varchar](255) NULL,
	[LinkedInURL] [varchar](255) NULL,
	[GitHubURL] [varchar](255) NULL,
	[CareerObjective] [varchar](max) NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[PersonalInfoID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Projects]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Projects](
	[ProjectID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[ProjectTitle] [varchar](100) NULL,
	[ProjectLink] [varchar](255) NULL,
	[Organization] [varchar](100) NULL,
	[Description] [varchar](max) NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ProjectID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Resumes]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Resumes](
	[ResumeID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeTitle] [varchar](100) NULL,
	[Status] [varchar](20) NULL,
	[VisitorCount] [int] NULL,
	[DownloadCount] [int] NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ResumeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Skills]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Skills](
	[SkillID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[SkillType] [varchar](30) NULL,
	[SkillName] [varchar](100) NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[SkillID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WorkExperience]    Script Date: 01-01-2026 15:52:39 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WorkExperience](
	[ExperienceID] [int] IDENTITY(1,1) NOT NULL,
	[ResumeID] [int] NOT NULL,
	[CompanyName] [varchar](100) NULL,
	[JobRole] [varchar](100) NULL,
	[DateOfJoin] [date] NULL,
	[LastWorkingDate] [date] NULL,
	[Experience] [varchar](50) NULL,
	[CreatedDate] [datetime] NULL,
	[UpdatedDate] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ExperienceID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Certifications] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Education] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Interests] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[PersonalInformation] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Projects] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Resumes] ADD  DEFAULT ('Draft') FOR [Status]
GO
ALTER TABLE [dbo].[Resumes] ADD  DEFAULT ((0)) FOR [VisitorCount]
GO
ALTER TABLE [dbo].[Resumes] ADD  DEFAULT ((0)) FOR [DownloadCount]
GO
ALTER TABLE [dbo].[Resumes] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Skills] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[WorkExperience] ADD  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[Certifications]  WITH CHECK ADD  CONSTRAINT [FK_Certifications_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[Certifications] CHECK CONSTRAINT [FK_Certifications_Resume]
GO
ALTER TABLE [dbo].[Education]  WITH CHECK ADD  CONSTRAINT [FK_Education_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[Education] CHECK CONSTRAINT [FK_Education_Resume]
GO
ALTER TABLE [dbo].[Interests]  WITH CHECK ADD  CONSTRAINT [FK_Interests_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[Interests] CHECK CONSTRAINT [FK_Interests_Resume]
GO
ALTER TABLE [dbo].[PersonalInformation]  WITH CHECK ADD  CONSTRAINT [FK_Personal_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[PersonalInformation] CHECK CONSTRAINT [FK_Personal_Resume]
GO
ALTER TABLE [dbo].[Projects]  WITH CHECK ADD  CONSTRAINT [FK_Project_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[Projects] CHECK CONSTRAINT [FK_Project_Resume]
GO
ALTER TABLE [dbo].[Skills]  WITH CHECK ADD  CONSTRAINT [FK_Skill_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[Skills] CHECK CONSTRAINT [FK_Skill_Resume]
GO
ALTER TABLE [dbo].[WorkExperience]  WITH CHECK ADD  CONSTRAINT [FK_Work_Resume] FOREIGN KEY([ResumeID])
REFERENCES [dbo].[Resumes] ([ResumeID])
GO
ALTER TABLE [dbo].[WorkExperience] CHECK CONSTRAINT [FK_Work_Resume]
GO
