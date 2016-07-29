from sqlalchemy.orm import relationship
from webapp import db


class HistoryDownloadStatus(db.Model):
    __tablename__ = 'history_download_status'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    date = db.Column(db.Date(), index=True)  # UTC date
    partial = db.Column(db.Boolean())
    full = db.Column(db.Boolean())

    location = relationship('Location', back_populates='history_downloads')
