from database import Base, engine, SessionLocal
import models


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Skip seeding if data already exists
        if db.query(models.DBUsers).first() is not None:
            print("Database already seeded, skipping.")
            return

        # --- Users ---
        admin = models.DBUsers(UserName="admin", passwd="admin", is_admin=True)
        user1 = models.DBUsers(UserName="sebas", passwd="1234", is_admin=False)
        user2 = models.DBUsers(UserName="guest", passwd="guest", is_admin=False)

        db.add_all([admin, user1, user2])
        db.commit()
        db.refresh(admin)
        db.refresh(user1)
        db.refresh(user2)

        # --- Tags ---
        tag1 = models.DBTags(TagName="retro")
        tag2 = models.DBTags(TagName="abstract")
        tag3 = models.DBTags(TagName="raymarching")
        tag4 = models.DBTags(TagName="procedural")

        db.add_all([tag1, tag2, tag3, tag4])
        db.commit()
        db.refresh(tag1)
        db.refresh(tag2)
        db.refresh(tag3)
        db.refresh(tag4)

        # --- Shaders ---
        shader1 = models.DBShader(
            user_id=user1.UserId,
            ShaderName="Rainbow Diagonal",
            ShaderCode="""#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

vec3 hsvToRgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0/3.0, 1.0/3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

void main() {
    float hue = fract((TexCoord.x + TexCoord.y) * 0.5 + uTime * 0.15);
    outputColor = vec4(hsvToRgb(vec3(hue, 1.0, 1.0)), 1.0);
}""",
        )

        shader2 = models.DBShader(
            user_id=user1.UserId,
            ShaderName="Solid Green",
            ShaderCode="""#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform float uTime;

void main() {
    outputColor = vec4(0.6, 0.7, 0.0, 1.0);
}""",
        )

        shader3 = models.DBShader(
            user_id=user2.UserId,
            ShaderName="Inverted Texture",
            ShaderCode="""#version 330 core
out vec4 outputColor;
in vec2 TexCoord;
uniform sampler2D texture0;
uniform float uTime;

void main() {
    vec4 tex = texture(texture0, TexCoord);
    outputColor = vec4(1.0 - tex.rgb, tex.a);
}""",

        )

        db.add_all([shader1, shader2, shader3])
        db.commit()
        db.refresh(shader1)
        db.refresh(shader2)
        db.refresh(shader3)

        # --- ShaderTags ---
        db.add_all([
            models.DBShaderTags(shader_id=shader1.ShaderId, tag_id=tag1.TagId, user_id=user1.UserId),
            models.DBShaderTags(shader_id=shader1.ShaderId, tag_id=tag2.TagId, user_id=user1.UserId),
            models.DBShaderTags(shader_id=shader2.ShaderId, tag_id=tag4.TagId, user_id=user1.UserId),
            models.DBShaderTags(shader_id=shader3.ShaderId, tag_id=tag2.TagId, user_id=user2.UserId),
            models.DBShaderTags(shader_id=shader3.ShaderId, tag_id=tag3.TagId, user_id=user2.UserId),
        ])
        db.commit()

        # --- Likes ---
        db.add_all([
            models.DBLikes(shader_id=shader1.ShaderId, user_id=user2.UserId),
            models.DBLikes(shader_id=shader1.ShaderId, user_id=admin.UserId),
            models.DBLikes(shader_id=shader2.ShaderId, user_id=user2.UserId),
            models.DBLikes(shader_id=shader3.ShaderId, user_id=user1.UserId),
        ])
        db.commit()

        # --- Comments ---
        db.add_all([
            models.DBComments(
                CommentText="Looks amazing!",
                CommentAuthor=user2.UserName,
                user_id=user2.UserId,
                shader_id=shader1.ShaderId,
            ),
            models.DBComments(
                CommentText="Nice colors.",
                CommentAuthor=admin.UserName,
                user_id=admin.UserId,
                shader_id=shader1.ShaderId,
            ),
            models.DBComments(
                CommentText="Cool inversion effect.",
                CommentAuthor=user1.UserName,
                user_id=user1.UserId,
                shader_id=shader3.ShaderId,
            ),
        ])
        db.commit()

        print("Database seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed, rolled back: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()