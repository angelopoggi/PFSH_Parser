import smtplib
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape


class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, template_dir: str = "templates"):
        """
        Initialize the EmailSender with SMTP settings and template directory.

        :param smtp_server: SMTP server address (e.g., smtp.office365.com).
        :param smtp_port: SMTP server port (e.g., 587).
        :param username: SMTP username/email address.
        :param password: SMTP password or app password.
        :param template_dir: Directory where Jinja templates are stored.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_template(self, template_name: str, context: dict) -> str:
        """
        Render a Jinja template with the provided context.

        :param template_name: Name of the template file (e.g., "email_template.html").
        :param context: Dictionary containing variables for the template.
        :return: Rendered template as a string.
        """
        template = self.env.get_template(template_name)
        return template.render(context)

    def send_email(self, subject: str, sender: str, recipients: list, body: str, html: bool = False) -> None:
        """
        Send an email using the SMTP server settings.

        :param subject: Subject of the email.
        :param sender: Email address of the sender.
        :param recipients: List of recipient email addresses.
        :param body: The email content.
        :param html: Whether the email content is HTML. Defaults to False.
        """
        # Choose MIME subtype
        mime_subtype = "html" if html else "plain"
        msg = MIMEText(body, mime_subtype)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.username, self.password)
                server.sendmail(sender, recipients, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_template_email(self, subject: str, sender: str, recipients: list, template_name: str,
                            context: dict) -> None:
        """
        Render a Jinja template and send it as an email.

        :param subject: Subject of the email.
        :param sender: Email address of the sender.
        :param recipients: List of recipient email addresses.
        :param template_name: Name of the Jinja template file.
        :param context: Dictionary containing variables for the template.
        """
        body = self.render_template(template_name, context)
        self.send_email(subject, sender, recipients, body, html=True)
