from fastapi import APIRouter, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.api.deps import AdminUser, CurrentUser, SessionDep
from app.core.images import prepare_photo
from app.core.security import hash_password
from app.models import (
    AdminStudentCreate,
    Student,
    StudentAdminRead,
    StudentCreate,
    StudentPhoto,
    StudentRead,
    StudentUpdate,
    User,
)

router = APIRouter(prefix="/students", tags=["Students"])

REQUIRED_FIELDS = ("name", "cgpa", "class_name", "start_date")
NO_CACHE = {"Cache-Control": "private, no-cache"}


# ---------- সাহায্যকারী ফাংশন ----------

def get_my_student(session: Session, user: User) -> Student:
    student = session.exec(
        select(Student).where(Student.user_id == user.id)
    ).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="আপনি এখনো প্রোফাইল তৈরি করেননি",
        )
    return student


def get_student_or_404(session: Session, student_id: int) -> Student:
    student = session.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="এই id-র student পাওয়া যায়নি",
        )
    return student


def to_admin_read(student: Student) -> StudentAdminRead:
    return StudentAdminRead.model_validate(
        student, update={"email": student.user.email}
    )


def apply_full_update(session: Session, student: Student, data: StudentCreate) -> Student:
    student.sqlmodel_update(data.model_dump())
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def apply_partial_update(session: Session, student: Student, data: StudentUpdate) -> Student:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="আপডেটের জন্য কোনো তথ্য পাঠানো হয়নি",
        )
    for field in REQUIRED_FIELDS:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} খালি রাখা যাবে না",
            )
    student.sqlmodel_update(update_data)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def store_photo(session: Session, student: Student, file: UploadFile) -> Student:
    jpeg = prepare_photo(file)
    if student.photo is None:
        student.photo = StudentPhoto(data=jpeg)
    else:
        student.photo.data = jpeg
    student.has_photo = True
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def clear_photo(session: Session, student: Student) -> Student:
    student.photo = None
    student.has_photo = False
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def photo_response(student: Student) -> Response:
    if student.photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="কোনো ছবি আপলোড করা নেই",
        )
    return Response(content=student.photo.data, media_type="image/jpeg", headers=NO_CACHE)


# ======================================================================
# Student: নিজের প্রোফাইল (/me রুটগুলো অবশ্যই /{student_id}-এর ওপরে থাকবে)
# ======================================================================

@router.post("/me", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_my_profile(data: StudentCreate, current_user: CurrentUser, session: SessionDep):
    existing = session.exec(
        select(Student).where(Student.user_id == current_user.id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="আপনার প্রোফাইল আগেই তৈরি করা আছে",
        )

    student = Student.model_validate(data, update={"user_id": current_user.id})
    session.add(student)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="আপনার প্রোফাইল আগেই তৈরি করা আছে",
        )
    session.refresh(student)
    return student


@router.get("/me", response_model=StudentRead)
def read_my_profile(current_user: CurrentUser, session: SessionDep):
    return get_my_student(session, current_user)


@router.put("/me", response_model=StudentRead)
def replace_my_profile(data: StudentCreate, current_user: CurrentUser, session: SessionDep):
    return apply_full_update(session, get_my_student(session, current_user), data)


@router.patch("/me", response_model=StudentRead)
def update_my_profile(data: StudentUpdate, current_user: CurrentUser, session: SessionDep):
    return apply_partial_update(session, get_my_student(session, current_user), data)


@router.put("/me/photo", response_model=StudentRead)
def upload_my_photo(file: UploadFile, current_user: CurrentUser, session: SessionDep):
    return store_photo(session, get_my_student(session, current_user), file)


@router.get("/me/photo")
def read_my_photo(current_user: CurrentUser, session: SessionDep):
    return photo_response(get_my_student(session, current_user))


@router.delete("/me/photo", response_model=StudentRead)
def delete_my_photo(current_user: CurrentUser, session: SessionDep):
    return clear_photo(session, get_my_student(session, current_user))


# ======================================================================
# Admin
# ======================================================================

@router.post("", response_model=StudentAdminRead, status_code=status.HTTP_201_CREATED)
def admin_create_student(data: AdminStudentCreate, _admin: AdminUser, session: SessionDep):
    email = data.email.lower()
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="এই ইমেইলে আগেই অ্যাকাউন্ট আছে",
        )

    user = User(email=email, hashed_password=hash_password(data.password))
    student = Student(**data.model_dump(exclude={"email", "password"}), user=user)
    session.add(student)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="এই ইমেইলে আগেই অ্যাকাউন্ট আছে",
        )
    session.refresh(student)
    return to_admin_read(student)


@router.get("", response_model=list[StudentAdminRead])
def list_students(
    _admin: AdminUser,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    students = session.exec(
        select(Student)
        .options(selectinload(Student.user))
        .order_by(Student.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return [to_admin_read(s) for s in students]


@router.get("/{student_id}", response_model=StudentAdminRead)
def admin_read_student(student_id: int, _admin: AdminUser, session: SessionDep):
    return to_admin_read(get_student_or_404(session, student_id))


@router.put("/{student_id}", response_model=StudentAdminRead)
def admin_replace_student(
    student_id: int, data: StudentCreate, _admin: AdminUser, session: SessionDep
):
    student = get_student_or_404(session, student_id)
    return to_admin_read(apply_full_update(session, student, data))


@router.patch("/{student_id}", response_model=StudentAdminRead)
def admin_update_student(
    student_id: int, data: StudentUpdate, _admin: AdminUser, session: SessionDep
):
    student = get_student_or_404(session, student_id)
    return to_admin_read(apply_partial_update(session, student, data))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, _admin: AdminUser, session: SessionDep):
    student = get_student_or_404(session, student_id)
    session.delete(student)
    session.commit()


@router.put("/{student_id}/photo", response_model=StudentAdminRead)
def admin_upload_photo(
    student_id: int, file: UploadFile, _admin: AdminUser, session: SessionDep
):
    student = get_student_or_404(session, student_id)
    return to_admin_read(store_photo(session, student, file))


@router.get("/{student_id}/photo")
def admin_read_photo(student_id: int, _admin: AdminUser, session: SessionDep):
    return photo_response(get_student_or_404(session, student_id))


@router.delete("/{student_id}/photo", response_model=StudentAdminRead)
def admin_delete_photo(student_id: int, _admin: AdminUser, session: SessionDep):
    student = get_student_or_404(session, student_id)
    return to_admin_read(clear_photo(session, student))